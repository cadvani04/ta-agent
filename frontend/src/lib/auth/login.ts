import { authClient } from './client'

export const signIn = async () => {
	await authClient.signIn.social({
		provider: 'google',
		callbackURL: '/dashboard'
		// errorCallbackURL: '/error',
		// newUserCallbackURL: '/welcome'
		// disableRedirect: true
	})
}

export const signOut = async () => {
	await authClient.signOut({
		fetchOptions: {
			onSuccess: () => {
				window.location.reload()
			}
		}
	})
}
