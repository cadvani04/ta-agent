import { db } from '@/server/db'
import type { Actions } from './$types'
import type { PageServerLoad } from './$types'
import { superValidate } from 'sveltekit-superforms'
import { zod } from 'sveltekit-superforms/adapters'
import * as table from '@/server/db/auth-schema'
import { prompt_creation } from '@/utils'

export const load: PageServerLoad = async ({ request, fetch, locals }) => {
	const courses = await db.select().from(table.course)

	// on server connect, fetch for new list of courses

	// const res = await fetch('/api/list_courses')

	// if (!res.ok) {
	// 	throw new Error(`Fetch failed: ${res.status}`)
	// }

	// const courseList = await res.json()

	// for (const course of courseList) {
	// 	console.log('course', course)
	// 	// check if course already exists in db
	// 	const existing = await db.select().from(table.course).where(eq(table.course.canvasId, course.id))

	// 	if (existing.length === 0) {
	// 		console.log('coursesss', existing, course.id)
	// 		// insert new course into db
	// 		if (locals.user) {
	// 			console.log('user', locals.user)
	// 		} else {
	// 			console.log('no user')
	// 		}

	// 		await db.insert(table.course).values({
	// 			canvasId: course.id,
	// 			courseName: course.name,
	// 			userId: locals.user?.id
	// 			// optional, for later
	// 			// discordId: course.discord_id,
	// 			// discordChannelId: course.discord_channel_id
	// 		})
	// 	}

	// 	// 	  {
	// 	//     id: 11883051,
	// 	//     name: 'CSE 30 Programming in Python',
	// 	//     account_id: 81259,
	// 	//     root_account_id: 10,
	// 	//     ...,
	// 	//   }
	// }

	return { courses }
}

export const actions = {
	query: async ({ request, fetch }) => {
		const form = await request.formData()

		const message = form.get('message')?.toString().trim()
		// const canvasId = form.get('canvasId')?.toString().trim()
		// const discordChannelId = form.get('discordChannelId')?.toString().trim()
		// const discordId = form.get('discordId')?.toString().trim()
		// const slackName = form.get('slackName')?.toString().trim()
		const prompt = form.get('prompt')?.toString().trim()
		const convoId = form.get('convoId')!.toString().trim()

		// console.log('form contents', message, canvasId, discordChannelId, discordId, slackName, prompt)

		// if (!message || !canvasId || !discordChannelId || !discordId || !slackName) {
		// 	return { success: false, error: 'Query cannot be empty' }
		// }

		// const final = prompt_creation(cocanvasId, discordChannelId, discordId, slackName) + message
		// console.log('final prompt', final)

		const res = await fetch('/api/agent', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				prompt
			})
		})
		const data = await res.json()

		console.log('results ::: ', data)

		// save to db
		await db.insert(table.msg).values({
			role: 'user',
			content: data,
			convoId
		})

		return {
			success: true,
			message, // user message
			response: data // ai response
		}
	}
} satisfies Actions
