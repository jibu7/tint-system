BEGIN;

CREATE TABLE IF NOT EXISTS public.color_rgb_values
(
    id serial NOT NULL,
    color_code character varying(50) COLLATE pg_catalog."default" NOT NULL,
    color_card character varying(50) COLLATE pg_catalog."default" NOT NULL,
    red integer NOT NULL CHECK (red BETWEEN 0 AND 255),
    green integer NOT NULL CHECK (green BETWEEN 0 AND 255),
    blue integer NOT NULL CHECK (blue BETWEEN 0 AND 255),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT color_rgb_values_pkey PRIMARY KEY (id),
    CONSTRAINT color_rgb_values_color_code_card_key UNIQUE (color_code, color_card)
);

-- Create an index on color_code for better query performance
CREATE INDEX IF NOT EXISTS idx_color_rgb_values_color_code
    ON public.color_rgb_values(color_code);

-- Create an index on color_card for better query performance
CREATE INDEX IF NOT EXISTS idx_color_rgb_values_color_card
    ON public.color_rgb_values(color_card);

COMMIT;
