import { pgTable, serial, text, timestamp, integer, boolean } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const books = pgTable('books', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  filename: text('filename').notNull(),
  totalPages: integer('total_pages').notNull(),
  processedPages: integer('processed_pages').default(0),
  fileData: text('file_data').notNull(), // Base64 PDF data
  thumbnail: text('thumbnail'), // First page as thumbnail
  createdAt: timestamp('created_at').defaultNow(),
  lastReadAt: timestamp('last_read_at').defaultNow(),
  currentPage: integer('current_page').default(1),
});

export const pages = pgTable('pages', {
  id: serial('id').primaryKey(),
  bookId: integer('book_id').notNull().references(() => books.id, { onDelete: 'cascade' }),
  pageNumber: integer('page_number').notNull(),
  extractedText: text('extracted_text'),
  isProcessed: boolean('is_processed').default(false),
  createdAt: timestamp('created_at').defaultNow(),
});

export const highlights = pgTable('highlights', {
  id: serial('id').primaryKey(),
  bookId: integer('book_id').notNull().references(() => books.id, { onDelete: 'cascade' }),
  pageNumber: integer('page_number').notNull(),
  selectedText: text('selected_text').notNull(),
  highlightId: text('highlight_id').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
});

export const booksRelations = relations(books, ({ many }) => ({
  pages: many(pages),
  highlights: many(highlights),
}));

export const pagesRelations = relations(pages, ({ one }) => ({
  book: one(books, {
    fields: [pages.bookId],
    references: [books.id],
  }),
}));

export const highlightsRelations = relations(highlights, ({ one }) => ({
  book: one(books, {
    fields: [highlights.bookId],
    references: [books.id],
  }),
}));

export type Book = typeof books.$inferSelect;
export type InsertBook = typeof books.$inferInsert;
export type Page = typeof pages.$inferSelect;
export type InsertPage = typeof pages.$inferInsert;
export type Highlight = typeof highlights.$inferSelect;
export type InsertHighlight = typeof highlights.$inferInsert;