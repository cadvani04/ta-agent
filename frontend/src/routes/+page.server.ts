import { auth } from '@/server/auth'
import type { PageServerLoad } from './$types'

export const load: PageServerLoad = async ({ request }) => {
	const session = await auth.api.getSession({
		headers: request.headers
	})
	return session
}
