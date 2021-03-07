// pages/admin_verify/admin_verify.js

var md5 = require("md5.js")
const app = getApp()
Page({

   /**
    * 页面的初始数据
    */
   data: {
      password: [],
   },

   /**
    * 生命周期函数--监听页面加载
    */
   onLoad: function (options) {
      var that = this
      wx.getStorage({
         key: 'password',
         success(res) {
            that.setData({
               password: res.data
            });
            if (that.password != "") {
               that.login();
            }
         }
      })

   },

   /**
    * 生命周期函数--监听页面初次渲染完成
    */
   onReady: function () {

   },

   /**
    * 生命周期函数--监听页面显示
    */
   onShow: function () {

   },

   /**
    * 生命周期函数--监听页面隐藏
    */
   onHide: function () {

   },

   /**
    * 生命周期函数--监听页面卸载
    */
   onUnload: function () {

   },

   /**
    * 页面相关事件处理函数--监听用户下拉动作
    */
   onPullDownRefresh: function () {

   },

   /**
    * 页面上拉触底事件的处理函数
    */
   onReachBottom: function () {

   },

   formInputChange(e) {
      wx.setStorage({
         key: "password",
         data: e.detail.value,
      });
      this.setData({
         password: e.detail.value,
      });
   },

   login() {
      var that = this
      if (this.data.password == "") {
         this.setData({
            error: "请输入密码"
         })
      } else {
         wx.showLoading({
            title: "登陆中",
            mask: true,
         });
         wx.request({
            url: 'https://www.bugstop.site/user/verify/',
            headers: {
               'Content-Type': 'application/json'
            },
            data: {
               password: md5.md5(this.data.password)
            },
            method: "POST",
            success(res) {
               if (res.data.statusCode == 200) {
                  wx.hideLoading();
                  app.globalData.admin_password = md5.md5(that.data.password);
                  wx.redirectTo({
                     url: '../admin/admin'
                  })
               } else {
                  wx.hideLoading();
                  that.setData({
                     error: "管理密码错误，请联系开发者",
                     password: ""
                  })
               }
            },
            fail() {
               wx.hideLoading();
               that.setData({
                  error: "登录超时，请稍候重试",
               })
            }
         })
      }
   }
})