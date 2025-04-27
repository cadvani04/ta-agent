import type { InsertMsg } from '@/server/db/auth-schema'

export class Convo {
	static id = crypto.randomUUID()
	isLoading = $state(false)
	messages: InsertMsg[] = $state([])

	constructor(msgs: InsertMsg[] = [], canvasId: string = '') {
		this.messages = msgs
	}

	addMsg = (msg: Omit<InsertMsg, 'convoId'>) => {
		this.messages.push({ ...msg, convoId: Convo.id })
	}

	flattenMsgs = () => {
		return this.messages.map(({ role, content }) => `${role}: ${content.trim()}`).join(' ')
	}

	convoId = () => {
		return Convo.id
	}

	reset() {
		this.messages = []
		this.isLoading = false
	}
}
