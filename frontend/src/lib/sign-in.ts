import { authClient } from '@/lib/auth-client' //import the auth client

await authClient.signIn.social({
	provider: 'github'
	callbackURL: '/dashboard',
	errorCallbackURL: '/error',
	newUserCallbackURL: '/welcome',
	/**
	 * disable the automatic redirect to the provider.
	 * @default false
	 */
	disableRedirect: true
})
