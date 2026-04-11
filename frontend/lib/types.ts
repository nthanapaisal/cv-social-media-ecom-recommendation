export interface VideoMetadata {
  video_id: string;
  video_path: string;
  duration_ms: number;
  caption?: string | null;
  bucket_num: string[];
  bucket_name: string[];
}

export interface ProductMetadata {
  product_id: string;
  product_path: string;
  title: string;
  product_details: string;
  bucket_num: string;
  bucket_name: string;
  price: number;
}

export interface CartItem {
  product: ProductMetadata;
  quantity: number;
}

export interface InteractionResponse {
  video_id: string;
  watch_time_ms: number;
  skipped_quickly: boolean;
  watched_50_pct: boolean;
  parquet_path: string;
}

export interface VideoUploadResponse {
  video_id: string;
  video_path: string;
  duration_ms: number;
  caption: string;
  bucket_num: string[] | null;
  bucket_name: string[] | null;
  status: UploadStatus;
  parquet_path: string;
}

export interface ProductUploadResponse {
  product_id: string;
  product_path: string;
  title: string;
  product_details: string;
  bucket_num: string;
  bucket_name: string;
  price: number;
  status: UploadStatus;
  parquet_path: string;
}

export type UploadStatus =
  | "completed"
  | "uploaded"
  | "uploaded_successful_but_failed_detect_classify";

export type ProductCategory =
  | "fashion"
  | "beauty"
  | "electronics"
  | "home"
  | "fitness"
  | "food"
  | "baby"
  | "automotive"
  | "pets"
  | "gaming";

export const PRODUCT_CATEGORIES: ProductCategory[] = [
  "fashion",
  "beauty",
  "electronics",
  "home",
  "fitness",
  "food",
  "baby",
  "automotive",
  "pets",
  "gaming",
];
