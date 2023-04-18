use std::{fs::File, io::Write};

use crate::types::Shape;
use crate::AUTHOR;
use crate::SUBTITLE;
use crate::TITLE;
use eyre::Result;

fn encode_shape(shape: &Shape) -> String {
    return match shape {
        Shape::Point(point) => format!("{},{}", point.x, point.y),
        Shape::Rect(rect) => format!(
            "{},{},{},{}",
            rect.top_left.x, rect.top_left.y, rect.bottom_right.x, rect.bottom_right.y
        ),
        Shape::Square(square) => format!(
            "{},{},{}",
            square.top_left.x, square.top_left.y, square.size
        ),
    };
}

pub fn write_info(
    width: i32,
    height: i32,
    titlescreen_image: &Vec<Shape>,
    total_chunks: u32,
) -> Result<()> {
    println!("Writing info...");

    let mut info_lua = File::create("bundle/SCRIPTS/BADAPPLE/info.lua")?;
    info_lua.write_all(format!("local title = \"{TITLE}\"\n").as_bytes())?;
    info_lua.write_all(format!("local subtitle = \"{SUBTITLE}\"\n").as_bytes())?;
    info_lua.write_all(format!("local author = \"{AUTHOR}\"\n").as_bytes())?;
    info_lua.write_all("local banner_image = {".as_bytes())?;
    for shape in titlescreen_image {
        info_lua.write_all(format!("{{{}}},", encode_shape(&shape)).as_bytes())?;
    }
    info_lua.write_all("}\n".as_bytes())?;
    info_lua.write_all(format!("local video_size = {{{},{}}}\n", width, height).as_bytes())?;
    info_lua.write_all(format!("local chunk_count = {total_chunks}\n").as_bytes())?;
    info_lua.write_all("return { title = title, subtitle = subtitle, author = author, banner_image = banner_image, video_size = video_size, chunk_count = chunk_count }".as_bytes())?;
    Ok(())
}

pub async fn write_chunks(video_data: Vec<Vec<Shape>>, max_size_kb: f32) -> Result<u32> {
    let mut frame_counter = 0;
    let mut chunk_counter = 0;
    let mut chunk_data = String::new();

    while frame_counter < video_data.len() {
        let frame = &video_data[frame_counter];
        let mut frame_data = "{".to_string();
        for shape in frame {
            frame_data.push_str(format!("{{{}}},", encode_shape(shape)).as_str());
        }
        frame_data.push_str("},");
        if chunk_data.len() + frame_data.len() >= (max_size_kb * 1000.0) as usize {
            println!("Writing chunk {chunk_counter}...");
            let mut chunk_lua =
                File::create(format!("bundle/SCRIPTS/BADAPPLE/chunk{chunk_counter}.lua"))?;
            chunk_lua
                .write_all(format!("local chunk = {{{chunk_data}}}\nreturn chunk").as_bytes())?;
            chunk_data.clear();
            chunk_counter += 1;
        } else {
            chunk_data.push_str(frame_data.as_str());
            frame_counter += 1
        }
    }
    Ok(chunk_counter)
}
