import type { ProductMetadata } from "./types";

const MOCK_PRODUCTS: ProductMetadata[] = [
  {
    product_id: "mock-001",
    product_path: "data/products/mock-001.jpg",
    title: "Classic Denim Jacket",
    product_details:
      "A timeless denim jacket perfect for layering in any season.",
    bucket_num: "01",
    bucket_name: "fashion",
  },
  {
    product_id: "mock-002",
    product_path: "data/products/mock-002.jpg",
    title: "Hydrating Face Serum",
    product_details:
      "Lightweight vitamin C serum for radiant and hydrated skin.",
    bucket_num: "02",
    bucket_name: "beauty",
  },
  {
    product_id: "mock-003",
    product_path: "data/products/mock-003.jpg",
    title: "Wireless Noise-Cancelling Headphones",
    product_details:
      "Premium over-ear headphones with 30-hour battery life and ANC.",
    bucket_num: "03",
    bucket_name: "electronics",
  },
  {
    product_id: "mock-004",
    product_path: "data/products/mock-004.jpg",
    title: "Scented Soy Candle Set",
    product_details: "Set of 3 hand-poured soy candles with calming scents.",
    bucket_num: "04",
    bucket_name: "home",
  },
  {
    product_id: "mock-005",
    product_path: "data/products/mock-005.jpg",
    title: "Resistance Band Set",
    product_details:
      "5-piece resistance band set for full-body home workouts.",
    bucket_num: "05",
    bucket_name: "fitness",
  },
  {
    product_id: "mock-006",
    product_path: "data/products/mock-006.jpg",
    title: "Organic Matcha Powder",
    product_details:
      "Premium ceremonial-grade matcha powder from Kyoto, Japan.",
    bucket_num: "06",
    bucket_name: "food",
  },
  {
    product_id: "mock-007",
    product_path: "data/products/mock-007.jpg",
    title: "Soft Plush Baby Blanket",
    product_details:
      "Ultra-soft hypoallergenic blanket for newborns and toddlers.",
    bucket_num: "07",
    bucket_name: "baby",
  },
  {
    product_id: "mock-008",
    product_path: "data/products/mock-008.jpg",
    title: "Car Phone Mount",
    product_details:
      "Universal magnetic car phone mount with 360-degree rotation.",
    bucket_num: "12",
    bucket_name: "automotive",
  },
  {
    product_id: "mock-009",
    product_path: "data/products/mock-009.jpg",
    title: "Interactive Cat Toy",
    product_details: "Automatic feather wand toy to keep cats entertained.",
    bucket_num: "09",
    bucket_name: "pets",
  },
  {
    product_id: "mock-010",
    product_path: "data/products/mock-010.jpg",
    title: "RGB Mechanical Keyboard",
    product_details:
      "Hot-swappable mechanical keyboard with per-key RGB lighting.",
    bucket_num: "10",
    bucket_name: "gaming",
  },
  {
    product_id: "mock-011",
    product_path: "data/products/mock-011.jpg",
    title: "Running Sneakers",
    product_details:
      "Lightweight cushioned running shoes for daily training.",
    bucket_num: "05",
    bucket_name: "fitness",
  },
  {
    product_id: "mock-012",
    product_path: "data/products/mock-012.jpg",
    title: "Portable Bluetooth Speaker",
    product_details: "Waterproof speaker with 12-hour battery and deep bass.",
    bucket_num: "03",
    bucket_name: "electronics",
  },
  {
    product_id: "mock-013",
    product_path: "data/products/mock-013.jpg",
    title: "Silk Pillowcase Set",
    product_details: "100% mulberry silk pillowcases for skin and hair care.",
    bucket_num: "04",
    bucket_name: "home",
  },
  {
    product_id: "mock-014",
    product_path: "data/products/mock-014.jpg",
    title: "Matte Lipstick Collection",
    product_details: "Set of 6 long-lasting matte lipsticks in trendy shades.",
    bucket_num: "02",
    bucket_name: "beauty",
  },
  {
    product_id: "mock-015",
    product_path: "data/products/mock-015.jpg",
    title: "Protein Powder Vanilla",
    product_details:
      "Plant-based protein powder with 25g protein per serving.",
    bucket_num: "06",
    bucket_name: "food",
  },
  {
    product_id: "mock-016",
    product_path: "data/products/mock-016.jpg",
    title: "Oversized Hoodie",
    product_details: "Cozy oversized hoodie in washed cotton with drop shoulders.",
    bucket_num: "01",
    bucket_name: "fashion",
  },
  {
    product_id: "mock-017",
    product_path: "data/products/mock-017.jpg",
    title: "Gaming Mouse Pad XL",
    product_details: "Extended desk pad with smooth surface and stitched edges.",
    bucket_num: "10",
    bucket_name: "gaming",
  },
  {
    product_id: "mock-018",
    product_path: "data/products/mock-018.jpg",
    title: "Dog Harness No-Pull",
    product_details: "Adjustable no-pull dog harness with reflective strips.",
    bucket_num: "09",
    bucket_name: "pets",
  },
];

export function getMockProducts(category?: string): ProductMetadata[] {
  if (category) {
    return MOCK_PRODUCTS.filter((p) => p.bucket_name === category);
  }
  return MOCK_PRODUCTS;
}
