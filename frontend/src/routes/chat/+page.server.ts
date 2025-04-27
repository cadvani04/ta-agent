import { db } from '@/server/db'
import type { Actions } from './$types'
import type { PageServerLoad } from './$types'
import { superValidate } from 'sveltekit-superforms'
import { zod } from 'sveltekit-superforms/adapters'
import * as table from '@/server/db/auth-schema'
import { ConsoleLogWriter, eq } from 'drizzle-orm'

export const load: PageServerLoad = async ({ request, fetch, locals }) => {
	// on server connect, fetch for new list of courses

	const res = await fetch('/api/list_courses')

	if (!res.ok) {
		throw new Error(`Fetch failed: ${res.status}`)
	}

	const courseList = await res.json()

	for (const course of courseList) {
		console.log('course', course)
		// check if course already exists in db
		const existing = await db.select().from(table.course).where(eq(table.course.canvasId, course.id))

		if (existing.length === 0) {
			console.log('coursesss', existing, course.id)
			// insert new course into db
			if (locals.user) {
				console.log('user', locals.user)
			} else {
				console.log('no user')
			}

			await db.insert(table.course).values({
				canvasId: course.id,
				courseName: course.name,
				userId: locals.user?.id
				// optional, for later
				// discordId: course.discord_id,
				// discordChannelId: course.discord_channel_id
			})
		}

		// 	  {
		//     id: 11883051,
		//     name: 'CSE 30 Programming in Python',
		//     account_id: 81259,
		//     root_account_id: 10,
		//     ...,
		//   }
	}

	return { courses: courseList }
}

export const actions = {
	query: async ({ request, fetch }) => {
		const form = await request.formData()
		const message = form.get('message')?.toString().trim()

		if (!message) {
			return { success: false, error: 'Query cannot be empty' }
		}

		console.log('message', message)

		const res = await fetch('/api/agent', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				prompt: message
			})
		})
		const data = await res.json()

		console.log('results:::', data)

		return {
			success: true,
			message, // user message
			response: data // ai response
		}
	}
} satisfies Actions
