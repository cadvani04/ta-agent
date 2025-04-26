import type { Actions } from './$types'
import type { PageServerLoad } from './$types'
import { superValidate } from 'sveltekit-superforms'
import { zod } from 'sveltekit-superforms/adapters'

export const load: PageServerLoad = async ({ request, fetch }) => {
	const res = await fetch('/api/basic')

	// console.log('res', res)

	if (!res.ok) {
		throw new Error(`Fetch failed: ${res.status}`)
	}

	const data = await res.json()
	return { data }
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
			response: data.result // ai response
		}
	}
} satisfies Actions
