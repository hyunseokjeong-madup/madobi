export const meta = { name: 'test-args', description: 'verify args transmission', phases: [{ title: 'x' }] }
log('args type: ' + typeof args)
const n = (args && args.items) ? args.items.length : -1
log('items length: ' + n)
return { argsType: typeof args, keys: args ? Object.keys(args) : null, n }
