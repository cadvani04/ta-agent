import { createAuthClient } from 'better-auth/svelte'

const authClient = createAuthClient({
	baseURL: import.meta.env.BETTER_AUTH_URL
})

export const logIn = async () => {
	await authClient.signIn.social({
		provider: 'google',
		callbackURL: '/dashboard'
		// errorCallbackURL: '/error',
		// newUserCallbackURL: '/welcome'
		// disableRedirect: true
	})
}

export const logOut = async () => {
	await authClient.signOut({
		fetchOptions: {
			onSuccess: () => {
				window.location.reload()
			}
		}
	})
}

export type Session = typeof authClient.$Infer.Session
