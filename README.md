<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/115161827/205339220-4adc3b2a-356b-480b-87d2-ae8e646c8216.png"/>  

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

App converts all supported labels to one bitmap for each supported class.
It may be helpful when you change your task from instance to semantic segmentation.

Supported classes: `Polygon`, `Bitmap` or `Any Shape` 

Supported labels: `Polygon`, `Bitmap`

All other shapes will be ignored, and will not be presenting in resulted project. 

You can convert object classes shapes using [convert-class-shape](https://ecosystem.supervise.ly/apps/convert-class-shape) application.

# How to use

App can be launched from ecosystem or images project

<details>
<summary open>Run from ecosystem</summary>
<br>

**Step 1.** Run the app from Ecosystem

<img src="https://user-images.githubusercontent.com/115161827/205343976-3a96f0c5-46f2-4277-bd9a-9e5c353bc951.png" width="80%" style='padding-top: 10px'>  

**Step 2.** Select input project and press the Run button

<img src="https://user-images.githubusercontent.com/115161827/205343993-fa83a96f-aa43-4f40-a801-f6b343bf0950.gif" width="80%" style='padding-top: 10px'>

</details>

<details>
<summary>Run from Images Project or Dataset</summary>
<br>

**Step 1.** Run the application from the context menu of the Images Project

<img src="https://user-images.githubusercontent.com/115161827/205345333-0b0a8c76-e369-406f-9955-46940f44e22a.png" width="80%" style='padding-top: 10px'>  

**Step 2.** Press the Run button

<img src="https://user-images.githubusercontent.com/115161827/205345339-112d4da7-fdfd-47f1-a5af-bea74f388119.png" width="80%" style='padding-top: 10px'>

</details>

# Result

Before(instance segmentation) |  After(semantic segmentation)
:-------------------------:|:-----------------------------------:
<img src="https://user-images.githubusercontent.com/115161827/205364201-9d7c781b-b464-488b-a4b5-2357290e7a67.png" style="max-height: 300px; width: auto;"/>  |  <img src="https://user-images.githubusercontent.com/115161827/205364209-b2ef0655-6b82-4157-b26a-338f3089e8e2.png" style="max-height: 300px; width: auto;"/>
