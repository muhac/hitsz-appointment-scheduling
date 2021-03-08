const app = getApp()

Page({
   data: {
      showTopTips: false,
      userInfo: [],

      sex: ["男", "女"],
      sexIndex: -1,

      dateIndex: -1,
      hourIndex: -1,
      hourItem: {},
      teacherIndex: -1,
      list: {},
      date_available: [],
      hour_available: [],

      length: 0,
      formData: {},
      rules: [{
         name: "wx",
         rules: {
            required: true,
            message: "连接服务器失败，请稍候重试",
         },
      },
         {
            name: "name",
            rules: {
               required: true,
               message: "请输入姓名",
            },
         },
         {
            name: "sex",
            rules: {
               required: true,
               message: "请选择性别",
            },
         },
         {
            name: "id",
            rules: {
               required: true,
               message: "学号为必填项",
            },
         },
         {
            name: "mobile",
            rules: [{
               required: true,
               message: "手机号码为必填项",
            },
               {
                  mobile: true,
                  message: "手机号码格式不正确",
               },
            ],
         },
         {
            name: "teacher",
            rules: [{
               required: true,
               message: "请选择一名辅导员",
            },],
         },
         {
            name: "date",
            rules: [{
               required: true,
               message: "请选择日期",
            },],
         },
         {
            name: "hour",
            rules: [{
               required: true,
               message: "请选择时间",
            },],
         }
      ],
   },

   onLoad: function (options) {
      var that = this;
      this.setData({
         userInfo: undefined, // app.globalData.userInfo,
         [`formData.wx`]: app.globalData.wx
      });
      wx.getStorage({
         key: "name",
         success(res) {
            that.setData({
               [`formData.name`]: res.data,
            });
         },
      });
      wx.getStorage({
         key: "sex",
         success(res) {
            that.setData({
               [`formData.sex`]: res.data,
            });
         },
      });
      wx.getStorage({
         key: "sexIndex",
         success(res) {
            that.setData({
               sexIndex: res.data,
            });
         },
      });

      wx.getStorage({
         key: "id",
         success(res) {
            that.setData({
               [`formData.id`]: res.data,
            });
         },
      });
      wx.getStorage({
         key: "mobile",
         success(res) {
            that.setData({
               [`formData.mobile`]: res.data,
            });
         },
      });
      wx.request({
         url: "https://www.bugstop.site/plan/empty/",
         headers: {
            "Content-Type": "application/json",
         },
         success(res) {
            //将获取到的json数据，存在名字叫list的这个数组中

            that.setData({
               list: res.data,
               //res代表success函数的事件对，data是固定的，list是数组
            });
            let data = that.data.list.schedule;
            var date_temp = [];
            for (var index in data) {
               var temp = 0;
               for (var index2 in data[index]) {
                  temp = temp + data[index][index2];
               }
               if (temp > 0) {
                  date_temp.push(index);
               }
               that.setData({
                  date_available: date_temp,
                  //res代表success函数的事件对，data是固定的，list是数组
               });
            }
         },
         fail() {
            wx.showToast({
               title: "连接超时，请稍候重试",
               icon: "error", //如果要纯文本，不要icon，将值设为'none'
               mask: true,
            });
         },
      });
   },

   textareaInput: function (e) {
      this.setData({
         length: e.detail.value.length,
         [`formData.detail`]: e.detail.value,
      });
   },

   bindTeacherChange: function (e) {
      var list = this.data.list;
      this.setData({
         teacherIndex: e.detail.value,
         [`formData.teacher`]: list.teachers[e.detail.value],
      });
   },

   bindDateChange: function (e) {
      var list = this.data.list;
      var date_available = this.data.date_available;
      var date_select = date_available[e.detail.value];

      var hour_temp = [];
      for (var index in list.schedule[date_select]) {
         if (list.schedule[date_select][index] > 0) {
            hour_temp.push(index);
         }
      }
      this.setData({
         dateIndex: e.detail.value,
         [`formData.date`]: date_select,
         hour_available: hour_temp,
      });
   },

   formInputChange(e) {
      const {
         field
      } = e.currentTarget.dataset;
      wx.setStorage({
         key: field,
         data: e.detail.value,
      });
      this.setData({
         [`formData.${field}`]: e.detail.value,
      });
   },

   bindHourChange: function (e) {
      var hour_available = this.data.hour_available;

      this.setData({
         hourIndex: e.detail.value,
         [`formData.hour`]: hour_available[e.detail.value],
      });
   },
   bindSexChange: function (e) {
      var sex = this.data.sex;
      wx.setStorage({
         key: "sexIndex",
         data: e.detail.value,
      });
      wx.setStorage({
         key: "sex",
         data: sex[e.detail.value],
      });
      this.setData({
         sexIndex: e.detail.value,
         [`formData.sex`]: sex[e.detail.value],
      });
   },

   submitForm() {
      var formdata = this.data.formData;
      var that = this;
      this.selectComponent("#form").validate((valid, errors) => {
         if (!valid) {
            const firstError = Object.keys(errors);
            if (firstError.length) {
               this.setData({
                  error: errors[firstError[0]].message,
               });
            }
         } else {
            if(that.data.formData.detail=="" || that.data.formData.detail==null){
               that.data.formData.detail="未填写";
            }
            wx.showLoading({
               title: "提交中",
               mask: true,
            });
            console.log("submit:", formdata);
            wx.request({
               url: "https://www.bugstop.site/plan/new/",
               data: formdata,
               headers: {
                  "Content-Type": "application/json",
               },
               timeout: 10000,
               method: "POST",
               success(res) {
                  wx.hideLoading();
                  switch (res.data.statusCode) {
                     case 200:
                        wx.showToast({
                           title: "预约成功",
                           icon: "success", //如果要纯文本，不要icon，将值设为'none'
                           mask: true,
                           duration: 3000,
                        });

                        setTimeout(function () {
                           wx.redirectTo({
                              url: "/pages/mybooks/mybooks",
                           });
                        }, 2000);
                        break;

                     case 500:
                        wx.showToast({
                           title: "预约失败，请重试",
                           icon: "error", //如果要纯文本，不要icon，将值设为'none'
                           mask: true,
                           duration: 3000,
                        });
                        break;
                  }
               },
               fail() {
                  wx.hideLoading();
                  wx.showToast({
                     title: "提交超时，请稍候重试",
                     icon: "error", //如果要纯文本，不要icon，将值设为'none'
                     mask: true,
                  });
               },
            });
         }
      });
   },
   /**
    * 用户点击右上角分享
    */
   onShareAppMessage: function () {

   },
});