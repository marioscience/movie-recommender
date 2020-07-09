FROM node:13-alpine

WORKDIR /usr/src/app

ENV PATH /usr/src/app/node_modules/.bin:${PATH}

COPY package.json ./
COPY package-lock.json ./

# Remove --silent for debugging
RUN npm install --silent
RUN npm install react-scripts@3.4.0 -g --silent

COPY . ./

EXPOSE 3000

CMD [ "npm", "start" ]
