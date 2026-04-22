from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"),
	       path('LoadDataset', views.LoadDataset, name="LoadDataset"),
	       path('TrainMLP', views.TrainMLP, name="TrainMLP"),
	       path('LoadDatasetAction', views.LoadDatasetAction, name="LoadDatasetAction"),	   
	       path('TrainAFFN', views.TrainAFFN, name="TrainAFFN"),
	       path('TrainLSTM', views.TrainLSTM, name="TrainLSTM"),
	       path('Graphs', views.Graphs, name="Graphs"), 	       
]