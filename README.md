<div align="center" markdown>
<img src="#баннер приложения"/>  

# Instance segmentation to semantic segmentation

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-use">How To Use</a> •
  <a href="#Result">Result</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/convert-to-semantic-segmentation)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/convert-to-semantic-segmentation)
<!-- [![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/convert-to-semantic-segmentation.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/convert-to-semantic-segmentation.png)](https://supervise.ly) -->

</div>

# Overview

App convert all supported labels to one bitmap for each supported class.
It may be helpful when you change you task from instance to semantic segmentation.

Supported classes: `Polygon`, `Bitmap` or `Any Shape` 

Supported labels: `Polygon`, `Bitmap`

All other shapes will be ignored, and will not be presenting in resulted project. 

You can convert object classes shapes using [convert-class-shape](https://ecosystem.supervise.ly/apps/convert-class-shape) application.

# How to use

App can be launched from ecosystem or images project

## Run from Ecosystem

**Step 1.** Run the app from Ecosystem

<img src="#action" width="80%" style='padding-top: 10px'>  

**Step 2.** Select input project and press the Run button

<img src="#action" width="80%" style='padding-top: 10px'>

## Run from Images Project or Dataset

**Step 1.** Run the application from the context menu of the Images Project

<img src="#action" width="80%" style='padding-top: 10px'>  

**Step 2.** Press the Run button

<img src="#action" width="80%" style='padding-top: 10px'>

# Result
## Project dataset (before)

<img src="#cкриншот из тулбокса для исходного датасета, где много аннотаций разных типов и есть одинаковые объекты" width="80%" style='padding-top: 10px'>

## Project dataset (after)

<img src="#cкриншот из тулбокса для результирующего датасета, где объекты одного класса объеденены одной аннотацией bitmap" width="80%" style='padding-top: 10px'>

## Project classes (before)

<img src="#cкриншот классов из исходного проекта" width="80%" style='padding-top: 10px'>

## Project classes (after)

<img src="#cкриншот классов из результирующего проекта(число классов <= исходному числу классов)" width="80%" style='padding-top: 10px'>

## Project objects statistics (before)

<img src="#cкриншот статистики по объектам из исходного проекта" width="80%" style='padding-top: 10px'>

## Project objects statistics (after)

<img src="#cкриншот статистики по объектам из результирующего проекта(число объектов < исходного числа объектов)" width="80%" style='padding-top: 10px'>