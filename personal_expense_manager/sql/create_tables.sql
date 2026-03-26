CREATE TABLE Expenses (
    ExpenseID INT PRIMARY KEY IDENTITY(1,1),
    Date DATE NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Description VARCHAR(255),
    Type VARCHAR(50),           
    Category VARCHAR(100),     
    SubCategory VARCHAR(100),  
    CreatedAt DATETIME DEFAULT GETDATE()
);


select * from Expenses  