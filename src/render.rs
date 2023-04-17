use std::collections::HashSet;

use crate::types::Direction;
use crate::types::Point;
use crate::types::Rect;
use crate::types::Shape;
use eyre::Result;
use opencv::core::Mat;
use opencv::prelude::*;

pub fn render_frame<F>(frame: &Mat, is_whitelisted: F) -> Result<Vec<Shape>>
where
    F: FnOnce(u8, u8, u8) -> bool + Copy,
{
    let height = frame.rows() as i16;
    let width = frame.cols() as i16;

    let center_pixel = Point {
        x: width / 2,
        y: height / 2,
    };

    let mut changed_pixels = HashSet::new();

    for x in 0..width {
        for y in 0..height {
            if is_whitelisted(*frame.at_2d::<u8>(y as i32, x as i32)?, x as u8, y as u8) {
                changed_pixels.insert(Point { x, y });
            }
        }
    }

    let mut result: Vec<Shape> = vec![];

    while changed_pixels.len() > 0 {
        let closest = find_closest_pixel(&center_pixel, &changed_pixels);

        let mut rect = Rect {
            top_left: closest.clone(),
            bottom_right: closest.clone(),
        };

        let mut hit_max_right = false;
        let mut hit_max_left = false;
        let mut hit_max_top = false;
        let mut hit_max_bottom = false;

        let mut currently_expanding_to = Direction::Right;

        loop {
            // if there is nowhere to expand anymore
            if hit_max_right && hit_max_left && hit_max_top && hit_max_bottom {
                break;
            }
            match currently_expanding_to {
                Direction::Right => {
                    if !hit_max_right {
                        let top_p = Point {
                            x: rect.bottom_right.x + 1,
                            y: rect.top_left.y,
                        };
                        let bottom_p = Point {
                            x: rect.bottom_right.x + 1,
                            y: rect.bottom_right.y,
                        };
                        let pixels = pixels_in_rect(&top_p, &bottom_p);

                        hit_max_right = !pixels.is_subset(&changed_pixels);
                    }
                    if !hit_max_right {
                        rect.bottom_right.x += 1;
                    }
                    currently_expanding_to = Direction::Left;
                }
                Direction::Left => {
                    if !hit_max_left {
                        let top_p = Point {
                            x: rect.top_left.x - 1,
                            y: rect.top_left.y,
                        };
                        let bottom_p = Point {
                            x: rect.top_left.x - 1,
                            y: rect.bottom_right.y,
                        };
                        let pixels = pixels_in_rect(&top_p, &bottom_p);

                        hit_max_left = !pixels.is_subset(&changed_pixels);
                    }
                    if !hit_max_left {
                        rect.top_left.x -= 1;
                    }
                    currently_expanding_to = Direction::Top;
                }
                Direction::Top => {
                    if !hit_max_top {
                        let left_p = Point {
                            x: rect.top_left.x,
                            y: rect.top_left.y - 1,
                        };
                        let right_p = Point {
                            x: rect.bottom_right.x,
                            y: rect.top_left.y - 1,
                        };
                        let pixels = pixels_in_rect(&left_p, &right_p);

                        hit_max_top = !pixels.is_subset(&changed_pixels);
                    }
                    if !hit_max_top {
                        rect.top_left.y -= 1;
                    }
                    currently_expanding_to = Direction::Bottom;
                }
                Direction::Bottom => {
                    if !hit_max_bottom {
                        let left_p = Point {
                            x: rect.top_left.x,
                            y: rect.bottom_right.y + 1,
                        };
                        let right_p = Point {
                            x: rect.bottom_right.x,
                            y: rect.bottom_right.y + 1,
                        };
                        let pixels = pixels_in_rect(&left_p, &right_p);

                        hit_max_bottom = !pixels.is_subset(&changed_pixels);
                    }
                    if !hit_max_bottom {
                        rect.bottom_right.y += 1;
                    }
                    currently_expanding_to = Direction::Right;
                }
            }
        }

        let pixels = pixels_in_rect(&rect.top_left, &rect.bottom_right);
        changed_pixels = changed_pixels.difference(&pixels).cloned().collect();

        result.push(Shape::Rect(rect));
    }

    result = result
        .into_iter()
        .map(|shape| {
            match shape {
                Shape::Rect(rect) => {
                    if rect.top_left == rect.bottom_right {
                        return Shape::Point(rect.top_left);
                    }
                    // TODO: Implement square generation
                    // old python code
                    // if rect.bottom_right.x - rect.top_left.x == rect.bottom_right.y - rect.top_left.y: # two same sides, can be a square
                    //     result[i] = Square(rect.top_left.x, rect.top_left.x, rect.bottom_right.x - rect.top_left.x)
                }
                _ => {}
            }
            shape
        })
        .collect();

    Ok(result)
}

pub fn find_closest_pixel(pixel: &Point, pixels: &HashSet<Point>) -> Point {
    let mut closest_distance = f32::INFINITY;
    let mut closest_pixel = None;

    for other_pixel in pixels {
        let distance = f32::sqrt(
            (pixel.x as f32 - other_pixel.x as f32).powi(2)
                + (pixel.y as f32 - other_pixel.y as f32).powi(2),
        );
        if distance < closest_distance {
            closest_distance = distance;
            closest_pixel = Some(other_pixel.clone());
        }
    }

    closest_pixel.unwrap() // will not fail
}

pub fn are_colors_different(first: u8, second: u8) -> bool {
    if first > second {
        first - second > 100
    } else {
        second - first > 100
    }
}

pub fn pixels_in_rect(top_left: &Point, bottom_right: &Point) -> HashSet<Point> {
    let mut pixels = HashSet::new();
    let x_min = top_left.x;
    let y_min = top_left.y;
    let x_max = bottom_right.x;
    let y_max = bottom_right.y;

    for x in x_min..=x_max {
        for y in y_min..=y_max {
            pixels.insert(Point { x, y });
        }
    }

    pixels
}

// pub fn adjacent_pixels(pixel: &Point, whitelist: &[Point]) -> Vec<Point> {
//     let x = pixel.x;
//     let y = pixel.y;
//     let adjacent_pixels = vec![
//         Point { x: x - 1, y },
//         Point { x: x + 1, y },
//         Point { x, y: y - 1 },
//         Point { x, y: y + 1 },
//         Point { x: x - 1, y: y - 1 },
//         Point { x: x + 1, y: y - 1 },
//         Point { x: x - 1, y: y + 1 },
//         Point { x: x + 1, y: y + 1 },
//     ];
//     adjacent_pixels
//         .into_iter()
//         .filter(|p| whitelist.contains(p))
//         .collect()
// }
