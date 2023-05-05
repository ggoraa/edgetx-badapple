mod config;
mod gen;
mod render;
mod types;

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

#[tokio::main(flavor = "multi_thread", worker_threads = 10)]
async fn main() -> Result<()> {
    let mut video = VideoCapture::from_file("badapple-qx7.mp4", CAP_ANY)?;
    let frame_count = video.get(CAP_PROP_FRAME_COUNT)? as u64;
    let frame_height = video.get(CAP_PROP_FRAME_HEIGHT)? as i32;
    let frame_width = video.get(CAP_PROP_FRAME_WIDTH)? as i32;

    let mut video_data: Vec<Vec<Shape>> = vec![];
    let mut prev_frame = Mat::new_rows_cols_with_default(
        frame_height,
        frame_width,
        opencv::core::CV_8UC1,
        Scalar::new(u8::MAX as f64, 0.0, 0.0, 0.0),
    )?;
    let mut titlescreen_image: Vec<Shape> = vec![];

    loop {
        let mut frame = Mat::default();
        let ret = video.read(&mut frame)?;
        if !ret {
            break;
        }
        let mut frame_grayscale = Mat::default();
        cvt_color(&frame, &mut frame_grayscale, COLOR_BGR2GRAY, 0)?;
        let frame = frame_grayscale;

        let current_frame = video.get(CAP_PROP_POS_FRAMES)? as u64;
        println!(
            "Rendering frame {current_frame}/{frame_count} ({:.2}%)",
            current_frame as f32 / frame_count as f32 * 100.0
        );

        if current_frame == TITLESCREEN_IMAGE_FRAME {
            titlescreen_image = render_frame(&frame, |p, _, _| p < 100)?;
        }

        let rendered_frame = render_frame(&frame, |p, x, y| {
            let loc = prev_frame.at_2d::<u8>(y as i32, x as i32);
            let loc = loc.unwrap();
            let loc = *loc;
            are_colors_different(loc, p)
        })?;
        prev_frame = frame;
        video_data.push(rendered_frame);
    }

    let total_chunks = write_chunks(video_data, VIDEO_CHUNK_SIZE_KB).await?;

    write_info(frame_width, frame_height, &titlescreen_image, total_chunks)?;

    Ok(())
}
