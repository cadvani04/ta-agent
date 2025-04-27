import { auth } from '@/server/auth'
import type { LayoutServerLoad } from './$types'

export const load: LayoutServerLoad = async ({ request, locals }) => {
	const session = await auth.api.getSession({
		headers: request.headers
	})

	if (session) {
		locals.user = session?.user
		locals.session = session?.session
	}

	return session
}
