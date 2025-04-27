import { type InferInsertModel, type InferSelectModel, relations } from 'drizzle-orm'
import { boolean, integer, pgEnum, pgTable, text, timestamp, uuid } from 'drizzle-orm/pg-core'

export const user = pgTable('user', {
	id: text('id').primaryKey(),
	name: text('name').notNull(),
	email: text('email').notNull().unique(),
	emailVerified: boolean('email_verified').notNull(),
	image: text('image'),
	createdAt: timestamp('created_at').notNull(),
	updatedAt: timestamp('updated_at').notNull()
})

export const session = pgTable('session', {
	id: text('id').primaryKey(),
	expiresAt: timestamp('expires_at').notNull(),
	token: text('token').notNull().unique(),
	createdAt: timestamp('created_at').notNull(),
	updatedAt: timestamp('updated_at').notNull(),
	ipAddress: text('ip_address'),
	userAgent: text('user_agent'),
	userId: text('user_id').notNull().references(() => user.id, { onDelete: 'cascade' })
})

export const account = pgTable('account', {
	id: text('id').primaryKey(),
	accountId: text('account_id').notNull(),
	providerId: text('provider_id').notNull(),
	userId: text('user_id').notNull().references(() => user.id, { onDelete: 'cascade' }),
	accessToken: text('access_token'),
	refreshToken: text('refresh_token'),
	idToken: text('id_token'),
	accessTokenExpiresAt: timestamp('access_token_expires_at'),
	refreshTokenExpiresAt: timestamp('refresh_token_expires_at'),
	scope: text('scope'),
	password: text('password'),
	createdAt: timestamp('created_at').notNull(),
	updatedAt: timestamp('updated_at').notNull()
})

export const verification = pgTable('verification', {
	id: text('id').primaryKey(),
	identifier: text('identifier').notNull(),
	value: text('value').notNull(),
	expiresAt: timestamp('expires_at').notNull(),
	createdAt: timestamp('created_at'),
	updatedAt: timestamp('updated_at')
})

export const course = pgTable('course', {
	canvasId: text('canvas_id').primaryKey().notNull(),
	courseName: text('course_name').notNull(),
	discordId: text('discord_id'), // discord server id
	discordChannelId: text('discord_channel_id'),
	userId: text('user_id').references(() => user.id, { onDelete: 'cascade' })
})

export const convo = pgTable('convo', {
	id: uuid('id').primaryKey().defaultRandom(),
	courseId: text('course_id').notNull().references(() => course.canvasId, { onDelete: 'cascade' }),
	createdAt: timestamp('created_at').notNull(),
	updatedAt: timestamp('updated_at').notNull()
})

export const roles = pgEnum('roles', ['user', 'agent'])

export const msg = pgTable('msg', {
	id: uuid('id').primaryKey().defaultRandom(),
	content: text('content').notNull(),
	role: roles('role').notNull(),
	convoId: text('convo_id').notNull().references(() => convo.id, { onDelete: 'cascade' }),
	createdAt: timestamp('created_at')
})

export type InsertUser = InferInsertModel<typeof user>
export type SelectUser = InferSelectModel<typeof user>

export type InsertSession = InferInsertModel<typeof session>
export type SelectSession = InferSelectModel<typeof session>

export type InsertCourse = InferInsertModel<typeof course>
export type SelectCourse = InferSelectModel<typeof course>

export type InsertMsg = InferInsertModel<typeof msg>
export type SelectMsg = InferSelectModel<typeof msg>

/// functionalities
// have many convos, each keeping track of previous conversations and their messages, passing in the last 5 messages to the next AI prompt for context
