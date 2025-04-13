FROM node:14-alpine

WORKDIR /app

# Don't try to copy function.js at build time
# Copy package.json if it exists
COPY package.json* .
RUN if [ -f package.json ]; then npm install; fi

# The actual function.js will be mounted at runtime
CMD ["node", "function.js"]