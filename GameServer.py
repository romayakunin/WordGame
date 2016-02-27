import urllib2
import socket
import threading


class Player(object):
    def __init__(self, game, connection):
        self.game = game
        self.connection = connection
        self.name = "Unnamed"
        self.score = 0

    def get_score_str(self):
        if self.score == 1: # 21, 31, ...
            s = "1 point."
        else:
            s = "%s points." % (self.score,)
        return s

    def process_next_message(self, message):
        game = self.game
        if not game.does_word_exist(message):
            return "Sorry, but your word doesn't exist, you have %s" % (self.get_score_str(),)
        if len(game.used_words) == 0:
            game.used_words.append(message)
            self.score += 1
            return "Ok, word chain lenght: 1, you have %s" % (self.get_score_str(),)
        if message[0] != game.used_words[-1][-1]:
            return "Sorry, but your word has to start with '%s', you have %s" % (
                game.used_words[-1][-1], self.get_score_str(),)
        if message in game.used_words:
            return "Sorry, but this word has already been used, you have %s" % (self.get_score_str(),)
        game.used_words.append(message)
        self.score += 1
        return "Ok, word chain length: %s, you have %s" % (len(game.used_words,), self.get_score_str(),)


class Game(object):
    def __init__(self):
         self.used_words = []
         self.players = []

    def does_word_exist(self, word):
        try:
            request = urllib2.Request("http://dictionary.reference.com/browse/%s" % (word,))
            response = urllib2.urlopen(request)
            return response.code in [200]
        except urllib2.HTTPError as e:
            return False

    def get_connected_player_count(self):
        count = 0
        for p in self.players:
            if p.connection is not None:
                count += 1
        return count


game = Game()
game_lock = threading.RLock()

listener = socket.socket()
address = (socket.gethostname(), 12345)
listener.bind(address)
listener.listen(5)

print "Server started."

connection_count = 0
while True:
    connection, addr = listener.accept()

    def serve_connection():
        player = Player(game, connection)
        game.players.append(player)
        try:
            print "Player #%s connected." % game.get_connected_player_count()
            while True:
                message = connection.recv(10000)
                if message == "/stop the game":
                    connection.send("Server shuts down.")
                    break
                with game_lock:
                    result = player.process_next_message(message)
                    connection.send(result)
        except Exception as e:
            print "Error:", e
        finally:
            try:
                connection.close()
                player.connection = None
                print "Player disconnected."
            except Exception as e:
                pass

    thread = threading.Thread(target=serve_connection)
    thread.start()
