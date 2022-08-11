FROM node:18.3 as builder
WORKDIR '/app'
COPY package.json .
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build