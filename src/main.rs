mod config;
mod gen;
mod render;
mod types;

use std::sync::Arc;

use crate::config::AUTHOR;
use crate::config::SUBTITLE;
use crate::config::TITLE;
use crate::gen::write_info;
use crate::{
    config::TITLESCREEN_IMAGE_FRAME,
    render::{are_colors_different, render_frame},
    types::Shape,
};
use config::VIDEO_CHUNK_SIZE_KB;
use eyre::Result;
use gen::write_chunks;
use opencv::{
    core::Scalar,
    imgproc::{cvt_color, COLOR_BGR2GRAY},
    prelude::*,
    videoio::{
        VideoCapture, CAP_ANY, CAP_PROP_FRAME_COUNT, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH,
        CAP_PROP_POS_FRAMES,
    },
};
use tokio::sync::Mutex;

#[tokio::main(flavor = "multi_thread", worker_threads = 10)]
async fn main() -> Result<()> {
    let mut video = VideoCapture::from_file("badapple-qx7.mp4", CAP_ANY)?;
    let frame_count = video.get(CAP_PROP_FRAME_COUNT)? as u64;
    let frame_height = video.get(CAP_PROP_FRAME_HEIGHT)? as i32;
    let frame_width = video.get(CAP_PROP_FRAME_WIDTH)? as i32;

    let mut video_data: Vec<Vec<Shape>> = vec![vec![]; frame_count as usize];
    let video_data = Arc::new(Mutex::new(video_data));
    let prev_frame = Arc::new(Mutex::new(Mat::new_rows_cols_with_default(
        frame_height,
        frame_width,
        opencv::core::CV_8UC1,
        Scalar::new(u8::MAX as f64, 0.0, 0.0, 0.0),
    )?));
    let titlescreen_image: Arc<Mutex<Vec<Shape>>> = Arc::new(Mutex::new(vec![]));

    let mut task_handles = vec![];

    loop {
        let mut frame = Mat::default();
        let ret = video.read(&mut frame)?;
        if !ret {
            break;
        }
        let current_frame = video.get(CAP_PROP_POS_FRAMES).unwrap() as u64;
        let frame = Arc::new(Mutex::new(frame));

        task_handles.push(tokio::spawn(render_step(
            prev_frame.clone(),
            video_data.clone(),
            titlescreen_image.clone(),
            frame_count,
            current_frame,
            frame
        )));
    }

    futures::future::join_all(task_handles).await;

    let total_chunks = write_chunks(video_data.lock().await.to_vec(), VIDEO_CHUNK_SIZE_KB).await?;

    let titlescreen_image = titlescreen_image.lock().await;

    write_info(frame_width, frame_height, &titlescreen_image, total_chunks)?;

    Ok(())
}

async fn render_step(
    prev_frame: Arc<Mutex<Mat>>,
    video_data: Arc<Mutex<Vec<Vec<Shape>>>>,
    titlescreen_image: Arc<Mutex<Vec<Shape>>>,
    frame_count: u64,
    current_frame: u64,
    frame: Arc<Mutex<Mat>>,
) {
    let mut frame_grayscale = Mat::default();
    let frame = frame.lock().await;
    cvt_color(&*frame, &mut frame_grayscale, COLOR_BGR2GRAY, 0).unwrap();
    let frame = Arc::new(Mutex::new(frame_grayscale));
    let frame = frame.lock().await;

    if current_frame == TITLESCREEN_IMAGE_FRAME {
        let mut titlescreen_image = titlescreen_image.lock().await;
        *titlescreen_image = render_frame(&*frame, |p, _, _| p < 100).unwrap();
    }

    let mut prev_frame = prev_frame.lock().await;
    
    println!(
        "Rendering frame {current_frame}/{frame_count} ({:.2}%)",
        current_frame as f32 / frame_count as f32 * 100.0
    );
    let rendered_frame = render_frame(&*frame, |p, x, y| {
        are_colors_different(*prev_frame.at_2d::<u8>(y as i32, x as i32).unwrap(), p)
    })
    .unwrap();
    *prev_frame = frame.clone();
    let mut video_data = video_data.lock().await;
    video_data[current_frame as usize] = rendered_frame;
}
