
# coding: utf-8

# In[ ]:

import numpy as np
import tensorflow as tf #OLD VERSION ##########UPDATE THIS##########
from othello import Board
from copy import deepcopy
import matplotlib.pyplot as plt

def reset_graph():
    if("sess" in globals() and sess):
        sess.close()
    tf.reset_default_graph()

def buildGraph(inputDim, dataType, hLayersDim, learning_rate = 5e-4, name="player"):
    with tf.variable_scope(name) as scope:
        x = tf.placeholder(dataType, [None, inputDim])
        actions = tf.placeholder(dataType, [None, inputDim])
        rewards = tf.placeholder(dataType, [None])

        layers = []
        biases = []

        # for i, dim in enumerate(hLayersDim):
        #     if i == 0:
        #         layers.append(tf.Variable("W"+str(i), dataType, [inputDim, dim]))
        #     elif i == len(hLayersDim) - 1:
        #         layers.append(tf.Variable("W"+str(i), dataType, [dim, inputDim]))
        #     else:
        #         layers.append(tf.Variable("W"+str(i), dataType, [hLayersDim[i-1], dim]))
        #     biases.append(tf.Variable("b"+str(i), dataType, [dim]))

        # for i, dim in enumerate(hLayersDim):
        #     activations.append(tf.nn.relu())

        layers.append(tf.get_variable("W0", [inputDim, hLayersDim[0]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        layers.append(tf.get_variable("W1", [hLayersDim[0], hLayersDim[1]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        layers.append(tf.get_variable("W2", [hLayersDim[1], hLayersDim[2]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        layers.append(tf.get_variable("W3", [hLayersDim[2], inputDim], dataType, initializer=tf.contrib.layers.xavier_initializer()))

        biases.append(tf.get_variable("b0", [hLayersDim[0]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        biases.append(tf.get_variable("b1", [hLayersDim[1]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        biases.append(tf.get_variable("b2", [hLayersDim[2]], dataType, initializer=tf.contrib.layers.xavier_initializer()))
        biases.append(tf.get_variable("b3", [inputDim], dataType, initializer=tf.contrib.layers.xavier_initializer()))

        hiddenStates = []

        hiddenStates.append(tf.nn.relu(tf.matmul(x, layers[0]) + biases[0])) #Olhar o relu6, pode ser melhor
        hiddenStates.append(tf.nn.relu(tf.matmul(hiddenStates[-1], layers[1]) + biases[1])) #Olhar o relu6, pode ser melhor
        hiddenStates.append(tf.nn.relu(tf.matmul(hiddenStates[-1], layers[2]) + biases[2])) #Olhar o relu6, pode ser melhor
        hiddenStates.append(tf.matmul(hiddenStates[-1], layers[3]) + biases[3]) #Olhar o relu6, pode ser melhor

        output_raw = hiddenStates[-1] #sparse_softmax_cross_entropy_with_logits
        output = tf.nn.softmax(output_raw)

        loss = tf.losses.softmax_cross_entropy(actions, output_raw, rewards)
        
        train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)
        
        return {
            "name": name,
            "x": x,
            "actions": actions,
            "rewards": rewards,
            "loss": loss,
            "layers": layers,
            "biases": biases,
            "hiddenStates": hiddenStates,
            "output": output,
            "train_step": train_step
        }
    
def predict(agent, state):
    return sess.run(agent["output"], feed_dict={agent["x"]: state})

def makeMove(agent, board, name):
    if(name == "BLACK"):
        player = 1
        tempBoard = board.board
    else:
        player = -1
        tempBoard = board.inverted_board()
       
    moves = board.possible_moves(player) 
    if(len(moves) == 0):
        return (-1, player)
    probs = predict(agent, tempBoard.reshape([1,-1])).squeeze()
    
    new_probs = np.zeros(boardDim)
    for x, y, _ in moves:
        new_probs[x*8 + y] = probs[x*8 + y]
        
    new_probs = new_probs/np.sum(new_probs)
    
    selected_move = np.random.choice(boardDim, 1, p=new_probs)[0]
    
    board.move(selected_move//8, selected_move%8, player)
    
    return (selected_move, player)
        
def maybePrint(shouldI, s):
    if(shouldI):
        print(s)
    
def playGame(board, gamma, v = False):
    board.reset()
    
    boardHistoryP1 = []
    boardHistoryP2 = []
    moveSequenceP1 = []
    moveSequenceP2 = []
    
    maybePrint(v, b)
    while(not b.finished()):
        boardBeforeMoveP1 = deepcopy(board.board)
        P1Move = makeMove(p, b, "BLACK")[0]
        if(P1Move != -1):
            boardHistoryP1.append(boardBeforeMoveP1)
            moveSequenceP1.append(P1Move)
        
        boardBeforeMoveP2 = deepcopy(board.inverted_board())
        P2Move = makeMove(p, b, "WHITE")[0]
        if(P2Move != -1):
            boardHistoryP2.append(boardBeforeMoveP2)
            moveSequenceP2.append(P1Move)
        maybePrint(v, "====================")
        maybePrint(v, (moveSequenceP1[-1]//8, moveSequenceP1[-1]%8))
        maybePrint(v, b)
        maybePrint(v, "====================")
        maybePrint(v, (moveSequenceP2[-1]//8, moveSequenceP2[-1]%8))
        maybePrint(v, b)
    maybePrint(v, b.score())
    
    rewardSequenceP1 = []
    rewardSequenceP2 = []
    r = reward(board)
    
    for i in range(len(moveSequenceP1)):
        rewardSequenceP1.append(r* (gamma**i))
    
    for i in range(len(moveSequenceP2)):
        rewardSequenceP2.append(-r* (gamma**i))
        
    rewardSequenceP1.reverse()
    rewardSequenceP2.reverse()
    boardHistory = boardHistoryP1 + boardHistoryP2
    moveSequence = moveSequenceP1 + moveSequenceP2
    rewardSequence = rewardSequenceP1 + rewardSequenceP2
    
    return (boardHistory, moveSequence, rewardSequence)
    
def reward(board):
    if(np.sum(board.board) > 0):
        return 1
    elif(np.sum(board.board) < 0):
        return -1
    else:
        return 0
    
def idx2onehot(idx):
    onehots = np.zeros((len(idx), boardDim))
    count = 0
    for i in idx:
        onehots[count][i] = 1
        count+=1
    return onehots
    
def sampleBatch(mem, size):
    indexes = []
    while(len(indexes) < size):
        i = np.random.randint(0,len(mem["states"]))
        if i not in indexes:
            indexes.append(i)
            
    boards = [mem["states"][i]for i in indexes]
    actions = idx2onehot([mem["actions"][i]for i in indexes])
    rewards = [mem["rewards"][i]for i in indexes]
    return np.array(boards).reshape((size, boardDim)), actions, np.array(rewards)

reset_graph()

batchSize = 32
epochs = 100
gamma = 0.99
boardDim = 8*8
hLayersDim = [128, 256, 128]

b = Board()
p = buildGraph(boardDim, tf.float32, hLayersDim)
replayMemory = {
    "states": [],
    "actions": [],
    "rewards": []
}
losses = []

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    for j in range(epochs):
        for i in range(batchSize):
            boards, moves, rewards = playGame(b, gamma)
            replayMemory["states"].extend(boards)
            replayMemory["actions"].extend(moves)
            replayMemory["rewards"].extend(rewards)

            boards, actions, rewards = sampleBatch(replayMemory, batchSize)
            loss, _ = sess.run([p["loss"], p["train_step"]], feed_dict={p["x"]:boards, p["actions"]: actions, p["rewards"]:rewards})
            losses.append(loss)
        print("Erro: "+str(loss))

    plt.plot(losses)
    plt.show()
    

