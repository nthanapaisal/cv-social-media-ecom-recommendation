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
  form: FormData,
  onProgress?: (loaded: number, total: number) => void
): Promise<VideoUploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(e.loaded, e.total);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          console.log("Video upload response:", response);
          resolve(response);
        } catch {
          reject(new Error("Invalid response from server"));
        }
      } else {
        console.error("Video upload failed:", xhr.status, xhr.responseText);
        reject(new Error(xhr.responseText || "Upload failed"));
      }
    });

    xhr.addEventListener("error", () => {
      reject(new Error("Network error during upload"));
    });

    xhr.open("POST", `${API_BASE}/upload/video/`);
    xhr.send(form);
  });
}

export async function uploadProduct(
  form: FormData,
  onProgress?: (loaded: number, total: number) => void
): Promise<ProductUploadResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(e.loaded, e.total);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          console.log("Product upload response:", response);
          resolve(response);
        } catch {
          reject(new Error("Invalid response from server"));
        }
      } else {
        console.error("Product upload failed:", xhr.status, xhr.responseText);
        reject(new Error(xhr.responseText || "Upload failed"));
      }
    });

    xhr.addEventListener("error", () => {
      reject(new Error("Network error during upload"));
    });

    xhr.open("POST", `${API_BASE}/upload/product/`);
    xhr.send(form);
  });
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
