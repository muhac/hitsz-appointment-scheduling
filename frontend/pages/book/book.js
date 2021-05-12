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
      dataSchool: {},
      dataSchedule: {},
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
            }, ],
         },
         {
            name: "date",
            rules: [{
               required: true,
               message: "请选择日期",
            }, ],
         },
         {
            name: "hour",
            rules: [{
               required: true,
               message: "请选择时间",
            }, ],
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
         url: "https://www.bugstop.site/plan/open/school",
         headers: {
            "Content-Type": "application/json",
         },

         success(res) {
            that.setData({
               dataSchool: res.data,
               dataSchedule: {
                  'statusCode': 400,
                  'dates': ["请先选择学院和辅导员"],
                  'hours': {
                     "请先选择学院和辅导员": ["请先选择学院和辅导员"],
                  }
               },
            });

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

   bindSchoolChange: function (e) {
      var dataSchool = this.data.dataSchool;

      this.setData({
         schoolIndex: e.detail.value,
         teacherIndex: -1,
         dateIndex: -1,
         hourIndex: -1,
         teacher_available: dataSchool.teachers[dataSchool.schools[e.detail.value]].辅导员,
         [`formData.school`]: dataSchool.schools[e.detail.value],
      });
   },

   bindTeacherChange: function (e) {
      var that = this;
      var teacher = this.data.teacher_available;

      this.setData({
         teacherIndex: e.detail.value,
         dateIndex: -1,
         hourIndex: -1,
         [`formData.teacher`]: teacher[e.detail.value],
      });

      wx.request({
         url: "https://www.bugstop.site/plan/open/schedule?school=" + that.data.formData.school + "&teacher=" + that.data.formData.teacher,
         headers: {
            "Content-Type": "application/json",
         },
         success(res) {
            that.setData({
               dataSchedule: res.data,
            });
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

   bindDateChange: function (e) {
      var dataSchedule = this.data.dataSchedule;

      this.setData({
         dateIndex: e.detail.value,
         hourIndex: -1,
         hour_available: dataSchedule.hours[dataSchedule.dates[e.detail.value]],
         [`formData.date`]: dataSchedule.dates[e.detail.value],
      });
   },

   bindHourChange: function (e) {
      var hour_available = this.data.hour_available;

      this.setData({
         hourIndex: e.detail.value,
         [`formData.hour`]: hour_available[e.detail.value],
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
            if (that.data.formData.detail == "" || that.data.formData.detail == null) {
               that.data.formData.detail = "未填写";
            }
            wx.showLoading({
               title: "提交中",
               mask: true,
            });
            console.log("submit:", formdata);
            wx.request({
               url: "https://www.bugstop.site/plan/open/",
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