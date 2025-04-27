import type { SelectSession, SelectUser } from '$lib/server/db/auth-schema'

// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		interface Locals {
			user: import('better-auth').User | null
			session: import('better-auth').Session | null
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
		interface FileUploadResponse {
			success: boolean
			jobs?: any[]
			image_urls?: string[]
			message?: string
		}

		interface FormResponse {
			form: any
			success?: boolean
		}

		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {}
