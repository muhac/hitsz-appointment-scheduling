// index.js
// 获取应用实例
const app = getApp()

Page({
  data: {
    mask_show:true,
    motto: 'Hello World',
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    code:[],
  },
  // 事件处理函数
  bindViewTap() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  gotoAdmin() {
    wx.navigateTo({
      url: '../admin_verify/admin_verify'
    })
  },
  gotoBook() {
    wx.navigateTo({
      url: '../book2/book2'
    })
  },
  onLoad:function() {
    var that=this
    console.log("hi")
    //登录
    wx.login({
      success(res){
        wx.request({
          url: 'https://www.bugstop.site/uid/',
          headers: {
            'Content-Type': 'application/json'
        },
          data:res,
          method:"POST",
          timeout:10000,
          success(res){
            console.log(res.data)
          }
        })
      },
      fail(){
        console.log("fail")
      }
    })
  },


})