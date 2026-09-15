import { z } from "zod/v3";

const id = z.string().min(1).max(80);
const item = z
  .object({
    id,
    title: z.string().min(1).max(160),
    summary: z.string().max(1000).optional(),
    topic: z.string().max(40).optional(),
  })
  .strict();

export function validateData(view, data) {
  if (view === "custom") return;
  const schema =
    view === "magazine"
      ? z
          .object({
            topics: z.array(z.string().min(1).max(40)).max(12),
            articles: z.array(item).max(30),
          })
          .strict()
      : z.object({ files: z.array(item).max(30) }).strict();
  schema.parse(data);
  const items = view === "magazine" ? data.articles : data.files;
  if (new Set(items.map((x) => x.id)).size !== items.length)
    throw new Error("Duplicate item id");
  if (
    view === "magazine" &&
    (new Set(data.topics).size !== data.topics.length ||
      items.some((x) => !data.topics.includes(x.topic)))
  )
    throw new Error("Invalid article topic");
}

function subset(values, allowed) {
  if (
    new Set(values).size !== values.length ||
    values.some((id) => !allowed.includes(id))
  ) {
    throw new Error("Selection contains duplicate or unknown values");
  }
}

export function validateState(panel, state) {
  if (panel.view === "custom") return;
  if (panel.view === "magazine") {
    z.object({
      topics: z.array(z.string()).max(12),
      saved: z.array(id).max(30),
      batch_size: z.number().int().min(1).max(8),
    })
      .strict()
      .parse(state);
    subset(state.topics, panel.data.topics);
    subset(
      state.saved,
      panel.data.articles.map((x) => x.id),
    );
  } else {
    z.object({ selected: z.array(id).max(30), order: z.array(id).max(30) })
      .strict()
      .parse(state);
    const ids = panel.data.files.map((x) => x.id);
    subset(state.selected, ids);
    subset(state.order, ids);
    if (state.order.length !== ids.length)
      throw new Error("File order must contain every supplied id");
  }
}
