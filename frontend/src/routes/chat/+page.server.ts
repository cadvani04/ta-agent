import { db } from '@/server/db'
import type { Actions } from './$types'
import type { PageServerLoad } from './$types'
import { superValidate } from 'sveltekit-superforms'
import { zod } from 'sveltekit-superforms/adapters'
import * as table from '@/server/db/auth-schema'
import { desc, eq } from 'drizzle-orm'
import { auth } from '@/server/auth'

export const load: PageServerLoad = async ({ request, fetch, locals }) => {
	// on server connect, fetch for course list, check for updates
	const courses = await db.select().from(table.course)

	const session = await auth.api.getSession({
		headers: request.headers
	})

	if (session) {
		locals.user = session?.user
		locals.session = session?.session
	}

	if (!locals.user) {
		return {
			courses: []
		}
	}

	// look and fetch history of messages
	// const past_msgs = await db.select().from(table.msg).where(eq(table.msg.userId, locals.user?.id)).orderBy(
	// 	table.msg.createdAt.desc()
	// )
	const msgHistory = await db.select().from(table.msg).where(eq(table.msg.userId, locals.user.id)).orderBy(
		desc(table.msg.createdAt)
	).limit(10)

	const conversations = msgHistory.reduce((acc: Record<string, any[]>, curr) => {
		if (!acc[curr.convoId]) {
			acc[curr.convoId] = []
		}
		acc[curr.convoId].push(curr.content)
		return acc
	}, {})

	console.log('msgHistory', msgHistory, 'conversations', conversations)

	return { courses, msgHistory, conversations }
}

export const actions = {
	query: async ({ request, fetch, locals }) => {
		const form = await request.formData()
		const message = form.get('message')?.toString().trim()
		const prompt = form.get('prompt')?.toString().trim()
		const context = form.get('context')?.toString().trim()
		const convoId = form.get('convoId')?.toString().trim()

		const session = await auth.api.getSession({
			headers: request.headers
		})

		if (session) {
			locals.user = session?.user
			locals.session = session?.session
		}

		console.log('to query to agent', prompt + (context ?? '') + message)

		const res = await fetch('/api/agent', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				prompt: prompt + (context ?? '') + message
			})
		})
		await db.insert(table.msg).values({
			role: 'user',
			content: message ?? '',
			convoId: convoId ?? '',
			userId: locals.user?.id
		})

		const data = await res.json()

		console.log('results ::: ', data)

		// save to db
		await db.insert(table.msg).values({
			role: 'agent',
			content: data,
			convoId: convoId ?? '',
			userId: locals.user?.id
		})

		return {
			success: true,
			message, // user message
			response: data // ai response
		}
	}
} satisfies Actions
