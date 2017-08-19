content = new Vue({
    el: "#content",
    data: {
        base_url: "http://localhost:8080",
        username:"",
        game:"",
        deck_size:"",
        discard_size:"",
        lastresponse: "",
        all_data:{},
        player_info:{}
    },
    methods:{
        createGame: function(){
            this.$http.post(
                this.base_url + '/api/create', 
                {"name":this.username}
            )
            .then(response => {
                this.game = response.body.game;
                this.update();
                this.hideLogin();
                window.setInterval(() => this.update(), 2000)
            }, response => {
                alert(JSON.stringify(response.body))
            });
        },
        joinGame: function(){
            this.$http.post(
                this.base_url + '/api/login', 
                {"name":this.username, "game":this.game}
            )
            .then(response => {
                this.update();
                this.hideLogin();
                window.setInterval(this.update(), 2000)
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        checkAccess: function(){
            this.$http.get(
                this.base_url + '/api/access'
            )
            .then(response => {
                this.game = response.body.game;
                this.update();
                this.hideLogin();
                window.setInterval(this.update(), 2000)
            }, response => {
                // Do nothing. We are just skipping auto login
            });
        },
        startGame: function(){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/start'
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        playCardFromHand: function(field){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/play/hand',
                {"field_index": field}
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        playCardFromMarket: function(card_id, field){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/play/market',
                {"field_index": field, "card_id": card_id}
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        playCardFromPending: function(card_id, field){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/play/pending',
                {"field_index": field, "card_id": card_id}
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        drawCardsToMarket: function(){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/draw/market'
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        drawCardsToHand: function(){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/draw/hand'
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        update: function(){
            this.$http.get(
                this.base_url + '/api/game/' + this.game
            )
            .then(response => {
                this.all_data = response.body;
                this.player_info = this.all_data.player_info;
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        createTrade: function(ids, other_players, wants){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/trade/create',
                {"card_ids":ids, "other_player":other_players, "wants":wants}
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        acceptTrade: function(trade_id, card_ids){
            this.$http.post(
                this.base_url + '/api/game/' + this.game + '/trade/accept',
                {"trade_id":trade_id, "card_ids":card_ids}
            )
            .then(response => {
                this.update()
            }, response => {
                alert(JSON.stringify(response.body.error))
            });
        },
        hideLogin: function(){
            document.getElementById("screen_overlay").className += " hidden";
        }
    },
    mounted: function(){
        this.checkAccess()
        console.log("MOUNTED")
    }
})