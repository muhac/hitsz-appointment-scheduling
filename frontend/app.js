// app.js
App({
   onLaunch() {
      var that = this
      wx.showLoading({
         title: "登陆中",
         mask: true,
      });
      // 登录
      wx.login({

         success: res => {
            // 发送 res.code 到后台换取 openId, sessionKey, unionId

            wx.request({
               url: 'https://www.bugstop.site/user/id/',
               headers: {
                  'Content-Type': 'application/json'
               },
               data: res,
               method: "POST",
               timeout: 10000,
               success(res) {
                  console.log(res.data)
                  if (res.statusCode == 200) {
                     wx.hideLoading();
                     that.globalData.wx = res.data.wx
                  } else {
                     wx.hideLoading();
                     wx.showToast({
                        title: "登录失败",
                        icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                        mask: true,
                        duration: 3000
                     })
                  }
               },
               fail() {
                  wx.hideLoading();
                  wx.showToast({
                     title: "连接超时",
                     icon: 'error', //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                     duration: 3000
                  })
               }
            })
         }
      })
      // 获取用户信息
      wx.getSetting({
         success: res => {
            if (res.authSetting['scope.userInfo']) {
               // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
               wx.getUserInfo({
                  success: res => {
                     // 可以将 res 发送给后台解码出 unionId
                     this.globalData.userInfo = res.userInfo

                     // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
                     // 所以此处加入 callback 以防止这种情况
                     if (this.userInfoReadyCallback) {
                        this.userInfoReadyCallback(res)
                     }
                  }
               })
            }
         }
      })
   },
   globalData: {
      userInfo: null,
      wx: null,
      admin_password: null
   }
})