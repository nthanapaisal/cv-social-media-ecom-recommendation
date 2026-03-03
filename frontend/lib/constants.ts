export const API_BASE = "/backend";

export const DIRECT_API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const VIDEO_EXTENSIONS = [".mp4", ".mov", ".mkv", ".webm", ".avi"];

export const FEED_PAGE_SIZE = 10;

export const BUCKET_LABELS: Record<string, string> = {
  "01": "Fashion",
  "02": "Beauty",
  "03": "Electronics",
  "04": "Home",
  "05": "Fitness",
  "06": "Food",
  "07": "Baby",
  "08": "Hobby",
  "09": "Pets",
  "10": "Gaming",
  "11": "Outdoor",
  "12": "Automotive",
  "13": "Other",
};

export const CATEGORY_COLORS: Record<string, string> = {
  fashion: "bg-pink-500/80",
  beauty: "bg-purple-500/80",
  electronics: "bg-blue-500/80",
  home: "bg-amber-500/80",
  fitness: "bg-green-500/80",
  food: "bg-orange-500/80",
  baby: "bg-rose-300/80",
  automotive: "bg-slate-500/80",
  pets: "bg-yellow-500/80",
  gaming: "bg-indigo-500/80",
  hobby: "bg-teal-500/80",
  outdoor: "bg-emerald-500/80",
  other: "bg-gray-500/80",
};
