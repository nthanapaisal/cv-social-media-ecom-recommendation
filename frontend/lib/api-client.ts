import { API_BASE } from "./constants";
import type {
  VideoMetadata,
  ProductMetadata,
  InteractionResponse,
  VideoUploadResponse,
  ProductUploadResponse,
} from "./types";

function normalizeFeedResponse(data: unknown): VideoMetadata[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === "object" && "videos" in data) {
    const obj = data as { videos: VideoMetadata[] };
    return Array.isArray(obj.videos) ? obj.videos : [];
  }
  return [];
}

export async function fetchFeed(vidsNum = 5): Promise<VideoMetadata[]> {
  const res = await fetch(`${API_BASE}/feed/videos?vids_num=${vidsNum}`);
  if (!res.ok) throw new Error(`Feed fetch failed: ${res.status}`);
  const data = await res.json();
  return normalizeFeedResponse(data);
}

export async function fetchVideoMetadata(
  id: string
): Promise<VideoMetadata> {
  const res = await fetch(`${API_BASE}/video/metadata/${id}`);
  if (!res.ok) throw new Error(`Video metadata fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchProductMetadata(
  id: string
): Promise<ProductMetadata> {
  const res = await fetch(`${API_BASE}/product/metadata/${id}`);
  if (!res.ok)
    throw new Error(`Product metadata fetch failed: ${res.status}`);
  return res.json();
}

export async function uploadVideo(
  form: FormData
): Promise<VideoUploadResponse> {
  const res = await fetch(`${API_BASE}/upload/video/`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Upload failed");
    throw new Error(text);
  }
  return res.json();
}

export async function uploadProduct(
  form: FormData
): Promise<ProductUploadResponse> {
  const res = await fetch(`${API_BASE}/upload/product/`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Upload failed");
    throw new Error(text);
  }
  return res.json();
}

export async function logInteraction(
  videoId: string,
  watchTimeMs: number
): Promise<InteractionResponse> {
  const res = await fetch(
    `${API_BASE}/video/interactions/?video_id=${encodeURIComponent(videoId)}&watch_time_ms=${watchTimeMs}`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error(`Interaction log failed: ${res.status}`);
  return res.json();
}

export async function fetchShopProducts(): Promise<ProductMetadata[]> {
  try {
    const res = await fetch(`${API_BASE}/shop/products`);
    if (!res.ok) return [];
    const data = await res.json();
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (data.products && Array.isArray(data.products)) return data.products;
    return [];
  } catch {
    return [];
  }
}

export function getVideoUrl(videoId: string): string {
  return `/api/media/videos/${videoId}`;
}

export function getProductImageUrl(productId: string): string {
  return `/api/media/products/${productId}`;
}
