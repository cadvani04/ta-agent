import type { InsertMsg } from '@/server/db/auth-schema'

export class Convo {
	static id = crypto.randomUUID()
	isLoading = $state(false)
	messages: InsertMsg[] = $state([])

	constructor(msgs: InsertMsg[]) {
		this.messages = msgs
	}

	addMsg = (msg: InsertMsg) => {
		this.messages.push(msg)
	}

	flattenMsgs = () => {
		return this.messages.map(({ role, content }) => `${role}: ${content.trim()}`).join(' ')
	}

	reset() {
		this.messages = []
		this.isLoading = false
	}
}
