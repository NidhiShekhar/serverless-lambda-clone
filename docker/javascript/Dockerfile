FROM node:14-alpine

WORKDIR /app
# encountered a stupid error where function.js was trying to get mounted at build time but thats WRONG.
#The actual functions needs to be mounted at run time.
# Copy package.json if it exists for party time

COPY package.json* .
RUN if [ -f package.json ]; then npm install; fi

# Mounting actual function.js at runtime
CMD ["node", "function.js"]
