// frontend/src/types/color.ts

export interface IColorantDetail {
  colorant_name: string;
  weight_g: number;
  volume_ml: number;
}

export interface IColorFormula {
  id: number;
  color_code: string;
  colorant_type?: string;
  color_series?: string;
  color_card?: string;
  paint_type?: string;
  base_paint?: string;
  packaging_spec?: string;
  colorant_details: IColorantDetail[];
  color_rgb?: {
    rgb: { r: number; g: number; b: number };
    hex: string;
  } | null;
  [key: string]: string | number | boolean | undefined | IColorantDetail[] | object | null;
}

export interface IApiError {
  detail: string;
  [key: string]: string | number | boolean | undefined | null;
}