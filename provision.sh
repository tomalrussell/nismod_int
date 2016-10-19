# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python-pip postgresql \
    postgresql-contrib postgis libpq-dev nginx-core python-dev \
    protobuf-compiler libprotobuf-dev

# Database config to listen on network connection
sed -i "s/#listen_address.*/listen_addresses 'localhost'/" \
    /etc/postgresql/9.5/main/postgresql.conf
# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"
# Add PostGIS extension
su vagrant -c "psql -c \"CREATE EXTENSION IF NOT EXISTS postgis;\" vagrant"

# Upgrade - with non-interactive flags so grub/sudo don't hang on config changes
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" -yq upgrade

# disable default site
rm /etc/nginx/sites-enabled/default
# copy config over
cp /vagrant/config/nginx.conf /etc/nginx/sites-available/nismod_int.conf
chmod 644 /etc/nginx/sites-available/nismod_int.conf
# enable dev site
ln -s /etc/nginx/sites-available/nismod_int.conf /etc/nginx/sites-enabled/nismod_int.conf
# set up nginx server
service nginx start
# reload nginx with config
service nginx reload

# upgrade pip
pip2 install --upgrade pip

# global install of python packages
pip2 install -r /vagrant/requirements.txt

# copy bash config to vagrant home
cp /vagrant/config/.bashrc /home/vagrant/.bashrc
chown vagrant:vagrant /home/vagrant/.bashrc
