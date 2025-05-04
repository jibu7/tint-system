// frontend/src/types/color.ts

// Matches backend schemas.ColorantDetail
export interface IColorantDetail {
  name: string;
  weight_g: number;
  volume_ml: number;
}

// Matches backend schemas.ColorFormulaResponse
export interface IColorFormula {
  color_code: string;
  color_series?: string | null;
  color_card?: string | null;
  paint_type?: string | null;
  base_paint?: string | null;
  colorants: IColorantDetail[];
}

// For handling API error responses
export interface IApiError {
  detail: string; // FastAPI often uses 'detail' for errors
}