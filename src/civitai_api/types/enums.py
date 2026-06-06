"""String literal enums for CivitAI API fields."""

from __future__ import annotations

from typing import Literal

ModelType = Literal[
    "Checkpoint",
    "TextualInversion",
    "Hypernetwork",
    "AestheticGradient",
    "LORA",
    "LoCon",
    "DoRA",
    "Controlnet",
    "Upscaler",
    "MotionModule",
    "VAE",
    "Poses",
    "Wildcards",
    "Workflows",
    "Detection",
    "Other",
]

BaseModel = Literal[
    "SD 1.4",
    "SD 1.5",
    "SD 1.5 LCM",
    "SD 1.5 Hyper",
    "SD 2.0",
    "SD 2.0 768",
    "SD 2.1",
    "SD 2.1 768",
    "SD 2.1 Unclip",
    "SDXL 0.9",
    "SDXL 1.0",
    "SDXL 1.0 LCM",
    "SDXL Distilled",
    "SDXL Turbo",
    "SDXL Lightning",
    "SDXL Hyper",
    "Pony",
    "Flux.1 S",
    "Flux.1 D",
    "AuraFlow",
    "AURAFLOW",
    "Illustrious",
    "Mochi",
    "LTXV",
    "CogVideoX",
    "HunyuanVideo",
    "Wan Video",
    "Other",
    "Unknown",
]

ModelSort = Literal[
    "Highest Rated",
    "Most Downloaded",
    "Newest",
    "Most Discussed",
    "Most Liked",
    "Most Collected",
    "Most Images",
    "New Team",
    "Oldest",
]

Period = Literal["AllTime", "Year", "Month", "Week", "Day"]

ImageSort = Literal[
    "Most Reactions",
    "Most Comments",
    "Newest",
    "Oldest",
]

NsfwLevel = Literal["None", "Soft", "Mature", "X"]

CommercialUse = Literal["None", "Image", "Rent", "Sell"]

SchedulerType = Literal[
    "Euler",
    "Euler a",
    "Heun",
    "DPM2",
    "DPM2 a",
    "DPM++ 2S a",
    "DPM++ 2M",
    "DPM++ SDE",
    "DPM fast",
    "DPM adaptive",
    "LMS Karras",
    "DPM2 Karras",
    "DPM2 a Karras",
    "DPM++ 2S a Karras",
    "DPM++ 2M Karras",
    "DPM++ SDE Karras",
    "DDIM",
    "PLMS",
    "UniPC",
    "LCM",
    "Other",
]
