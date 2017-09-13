content = new Vue({
    el: "#content",
    data: {
        base_url: location.protocol + '//' + window.location.hostname + ':8080',
        username:"",
        game:"",
        deck_size:"",
        discard_size:"",
        lastresponse: "",
        all_data:{},
        player_info:{},
        socket: null
    },
    methods:{
        createGame: function(){
            axios({
                method: 'post',
                url: this.base_url + '/api/create',
                data: {
                    "name":this.username,
                    "game_type":"public"
                },
                withCredentials: true
            })
            .then(response => {
                this.game = response.data.game;
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        joinGame: function(){
            axios({
                method: 'post',
                url: this.base_url + '/api/login',
                data: {
                    "name":this.username,
                    "game":this.game
                },
                withCredentials: true
            })
            .then(response => {
                this.game = response.data.game;
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        checkAccess: function(){
            axios({
                method: 'get',
                url: this.base_url + '/api/access',
                withCredentials: true
            })
            .then(response => {
                this.game = response.data.game;
                this.update();
            })
            .catch(error => {
                console.log("Could not login with cookie")
            });
        },
        startGame: function(){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/start',
                data: {
                    "name":this.username,
                    "game":this.game
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        playCardFromHand: function(field){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/play/hand',
                data: {
                    "field_index": field
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        playCardFromMarket: function(card_id, field){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/play/market',
                data: {
                    "field_index": field,
                    "card_id": card_id
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        playCardFromPending: function(card_id, field){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/play/pending',
                data: {
                    "field_index": field,
                    "card_id": card_id
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        drawCardsToMarket: function(){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/draw/market',
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        drawCardsToHand: function(){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/draw/hand',
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        update: function(){
            axios({
                method: 'get',
                url: this.base_url + '/api/game/' + this.game,
                withCredentials: true
            })
            .then(response => {
                this.all_data = response.data;
                this.player_info = this.all_data.player_info;
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        createTrade: function(ids, other_players, wants){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/trade/create',
                data: {
                    "card_ids":ids,
                    "other_player":other_players,
                    "wants":wants
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        acceptTrade: function(trade_id, card_ids){
            axios({
                method: 'post',
                url: this.base_url + '/api/game/' + this.game + '/trade/accept',
                data: {
                    "trade_id":trade_id,
                    "card_ids":card_ids
                },
                withCredentials: true
            })
            .then(response => {
                this.update();
            })
            .catch(error => {
                alert(JSON.stringify(error))
            });
        },
        socketConnect: function(){
            this.socket = io('http://localhost:8080');
            this.socket.on('client full', (data) => {console.log(data)});
            this.socket.on('client update', (data) => {console.log(data)})
            obj = {'game':content.game, 'token':getCookie('tbg_token')}
            this.socket.emit('login', obj)        
        },
    },
    mounted: function(){
        this.checkAccess()
    }
})
function getCookie(key){
    cookies = document.cookie.split(';');
    for (index in cookies){
        cookie = cookies[index]
        if(cookie.indexOf(key)>-1){
            return cookie.split('=')[1];
        }
    }
}