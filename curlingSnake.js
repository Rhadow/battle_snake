const bodyParser = require('body-parser')
const express = require('express')

const PORT = process.env.PORT || 3000

const app = express()
app.use(bodyParser.json())

app.get('/', handleIndex)
app.post('/start', handleStart)
app.post('/move', handleMove)
app.post('/end', handleEnd)

app.listen(PORT, () => console.log(`Battlesnake Server listening at http://127.0.0.1:${PORT}`))


function handleIndex(request, response) {
  var battlesnakeInfo = {
    apiversion: '1',
    author: '',
    color: '#888888',
    head: 'default',
    tail: 'default'
  }
  response.status(200).json(battlesnakeInfo)
}

function handleStart(request, response) {
  var gameData = request.body

  console.log('START')
  response.status(200).send('ok')
}

function handleMove(request, response) {
  const gameData = request.body
  const boardWidth = gameData.board.width;
  const boardHeight = gameData.board.height;
  const head = gameData.you.head;
  const neck = gameData.you.body[1];
  let move = 'up';
  if (head.y === boardHeight - 1) {
    if (head.x === 0) {
      move = 'down';
    } else {
      move = 'left';
    }
  } else if (head.x === boardWidth - 1) {
    if (head.y === boardHeight - 1) {
      move = 'left';
    } else {
      move = 'up';
    }
  } else if (head.y === 0) {
    if (neck.x === head.x + 1) {
      move = 'up';
    } else {
      move = 'right';
    }
  } else {
    if (head.y % 2 === 0) {
      if (neck.x === head.x + 1 || head.x === boardWidth - 2) {
        move = 'down';
      } else {
        move = 'right';
      }

    } else {
      if (neck.x === head.x - 1 || head.x === 0) {
        move = 'down';
      } else {
        move = 'left';
      }
    }
  }

  console.log('MOVE: ' + move)
  response.status(200).send({
    move: move
  })
}

function handleEnd(request, response) {
  var gameData = request.body

  console.log('END')
  response.status(200).send('ok')
}
