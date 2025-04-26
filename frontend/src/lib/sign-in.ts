import { authClient } from './client'

await authClient.signIn.social({
	provider: 'google',
	callbackURL: '/dashboard'
	// errorCallbackURL: '/error',
	// newUserCallbackURL: '/welcome'
	// disableRedirect: true
})
