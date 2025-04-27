import { auth } from '@/server/auth'
import { error, redirect } from '@sveltejs/kit'
import { svelteKitHandler } from 'better-auth/svelte-kit'
import type { Handle, HandleFetch } from '@sveltejs/kit'

export const handle: Handle = async ({ event, resolve }) => {
	// CSRF protection
	if (event.request.method !== 'GET') {
		const origin = event.request.headers.get('Origin')

		if (
			!origin ||
			origin !==
				(process.env.NODE_ENV == 'development' ? 'http://localhost:5173' : 'https://att.vercel.app')
		) {
			throw error(403, 'Forbidden: Invalid origin')
		}
	}

	if (!(event.url.pathname == '/' || event.url.pathname.startsWith('/api/auth'))) {
		// Check if the user is authenticated
		const session = await auth.api.getSession({
			headers: event.request.headers
		})

		// console.log('Session:', session)
		if (!session) throw redirect(302, '/')
	}

	return svelteKitHandler({ event, resolve, auth })
}

export const handleFetch: HandleFetch = async ({ request, fetch }) => {
	if (request.url.startsWith('http://localhost:5173/api')) {
		// clone the original request, but change the URL
		request = new Request(
			request.url.replace('http://localhost:5173/api', 'http://localhost:8000'),
			request
		)
	}

	return fetch(request)
}
