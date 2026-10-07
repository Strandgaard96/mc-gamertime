import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "./api";
import { preparePhoto, uploadSessionPhoto } from "./photos";

vi.mock("./api");

function mockCanvas(blobTypes: string[]) {
  const sizes: { w: number; h: number }[] = [];
  const types = [...blobTypes];
  vi.spyOn(document, "createElement").mockImplementation(((tag: string) => {
    if (tag !== "canvas") throw new Error(`unexpected ${tag}`);
    const canvas = {
      width: 0,
      height: 0,
      getContext: () => ({ drawImage: vi.fn() }),
      toBlob(cb: (b: Blob) => void, type: string) {
        sizes.push({ w: canvas.width, h: canvas.height });
        const actual = types.shift() ?? type;
        cb(new Blob(["x"], { type: actual }));
      },
    };
    return canvas;
  }) as typeof document.createElement);
  return sizes;
}

beforeEach(() => {
  vi.stubGlobal(
    "createImageBitmap",
    vi.fn().mockResolvedValue({ width: 4000, height: 3000, close: vi.fn() }),
  );
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("preparePhoto", () => {
  it("downscales the long edge to 2048 and encodes webp", async () => {
    const sizes = mockCanvas(["image/webp"]);
    const blob = await preparePhoto(new File(["x"], "a.jpg", { type: "image/jpeg" }));
    expect(blob.type).toBe("image/webp");
    expect(sizes[0]).toEqual({ w: 2048, h: 1536 });
    expect(createImageBitmap).toHaveBeenCalledWith(expect.any(File), {
      imageOrientation: "from-image",
    });
  });

  it("falls back to jpeg when the browser returns png for webp", async () => {
    mockCanvas(["image/png", "image/jpeg"]);
    const blob = await preparePhoto(new File(["x"], "a.jpg", { type: "image/jpeg" }));
    expect(blob.type).toBe("image/jpeg");
  });
});

describe("uploadSessionPhoto", () => {
  it("requests, PUTs with the blob's type, then confirms", async () => {
    vi.mocked(api.requestPhotoUpload).mockResolvedValue({
      uploadUrl: "/u",
      imageUrl: "/i",
      key: "session-photos/K.jpg",
    });
    vi.mocked(api.createPhoto).mockResolvedValue({ pk: "p" } as never);
    const fetchMock = vi.fn().mockResolvedValue({ ok: true });
    vi.stubGlobal("fetch", fetchMock);
    const blob = new Blob(["x"], { type: "image/jpeg" });
    await uploadSessionPhoto("s1", blob);
    expect(api.requestPhotoUpload).toHaveBeenCalledWith("s1", "image/jpeg");
    expect(fetchMock).toHaveBeenCalledWith("/u", {
      method: "PUT",
      body: blob,
      headers: { "Content-Type": "image/jpeg" },
    });
    expect(api.createPhoto).toHaveBeenCalledWith("s1", "session-photos/K.jpg");
  });

  it("throws and does not confirm when the PUT fails", async () => {
    vi.mocked(api.requestPhotoUpload).mockResolvedValue({ uploadUrl: "/u", imageUrl: "/i", key: "k" });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 413 }));
    await expect(uploadSessionPhoto("s1", new Blob(["x"], { type: "image/webp" }))).rejects.toThrow();
    expect(api.createPhoto).not.toHaveBeenCalled();
  });
});
