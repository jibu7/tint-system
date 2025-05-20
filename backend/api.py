
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example data (replace with your DB logic)
DATA = [
    {
        "color_code": "0011P",
        "colorant_type": "IYAGA COLOR PASTE",
        "color_series": "12 Color",
        "color_card": "KIPAU COLOR CHART",
        "paint_type": "IYG PAE(Weather Guard)",
        "base_paint": "BASE A",
        "packaging_spec": "1KG",
        "colorant_details": [
            {
                "colorant_name": "IYG YL OXD 2042",
                "weight_g": "0.5628000",
                "volume_ml": "0.3179661"
            },
            {
                "colorant_name": "IYG GRN G Y2154",
                "weight_g": "0.9380000",
                "volume_ml": "0.4509615"
            }
        ],
        "color_rgb": {
            "rgb": {
                "r": 253,
                "g": 242,
                "b": 231
            },
            "hex": "#fdf2e7"
        }
    },
    {
        "color_code": "0011P",
        "colorant_type": "IYAGA COLOR PASTE",
        "color_series": "12 Color",
        "color_card": "KIPAU COLOR CHART",
        "paint_type": "IYG VM WHITE",
        "base_paint": "BASE A",
        "packaging_spec": "1KG",
        "colorant_details": [
            {
                "colorant_name": "IYG YL OXD 2042",
                "weight_g": "0.5628000",
                "volume_ml": "0.3179661"
            },
            {
                "colorant_name": "IYG GRN G Y2154",
                "weight_g": "0.9380000",
                "volume_ml": "0.4509615"
            }
        ],
        "color_rgb": {
            "rgb": {
                "r": 253,
                "g": 242,
                "b": 231
            },
            "hex": "#fdf2e7"
        }
    },
    {
        "color_code": "0011P",
        "colorant_type": "IYAGA COLOR PASTE",
        "color_series": "12 Color",
        "color_card": "KIPAU COLOR CHART",
        "paint_type": "IYG VS CLASSIC & NORMAL",
        "base_paint": "BASE A",
        "packaging_spec": "1KG",
        "colorant_details": [
            {
                "colorant_name": "IYG YL OXD 2042",
                "weight_g": "0.6000000",
                "volume_ml": "0.3389831"
            },
            {
                "colorant_name": "IYG GRN G Y2154",
                "weight_g": "1.0000000",
                "volume_ml": "0.4807692"
            }
        ],
        "color_rgb": {
            "rgb": {
                "r": 253,
                "g": 242,
                "b": 231
            },
            "hex": "#fdf2e7"
        }
    }
]

@app.get("/api/formulation/{color_code}")
def get_formulation(color_code: str):
    results = [item for item in DATA if item["color_code"].lower() == color_code.lower()]
    if not results:
        raise HTTPException(status_code=404, detail="No formulations found")
    return results

@app.get("/")
async def read_root():
    return {"message": "API is working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
