create table urls(
    id int NOT NULL auto_increment,
    url varchar(100),
    primary key (id)
) engine=InnoDB default charset=utf8;


create user 'test'@'%' identified by 'mysql824.';

grant all on test.urls to 'test'@'%';