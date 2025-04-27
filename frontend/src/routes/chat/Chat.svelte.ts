class Todo {
	done = $state(false)
	text = $state()

	constructor(text: string) {
		this.text = text
	}

	reset() {
		this.text = ''
		this.done = false
	}
}
