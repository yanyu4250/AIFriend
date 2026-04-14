import  {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore('user', () => {
    const id =ref('0')
    const username =ref('')
    const photo =ref('')
    const profile =ref('')
    const accessToken =ref('')

    function isLogin(){
        return !!accessToken.value  //必须带value
    }

    function setAccessToken(token){
        accessToken.value = token
    }

    function setUserInfo(user){
        id.value = user.user_id
        username.value = user.username
        photo.value = user.photo
        profile.value = user.profile
    }

    function logout(){
        id.value = 0
        username.value = ''
        photo.value = ''
        profile.value = ''
        accessToken.value = ''
    }

    return {
        id,
        username,
        photo,
        profile,
        accessToken,    //不能忘记这个
        setAccessToken,
        setUserInfo,
        logout,
        isLogin
    }
})

